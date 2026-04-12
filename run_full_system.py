import os
import sys
import subprocess
import json
import time
import shutil

# set PYTHONPATH to current directory for imports
env = os.environ.copy()
env['PYTHONPATH'] = os.getcwd()


def check_command_exists(command):
    try:
        subprocess.run([command, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError:
        return True


def print_ollama_install_hint():
    print("Ollama is not installed. Install with:")
    print("Linux (Codespaces): curl -fsSL https://ollama.com/install.sh | sh")


def run_main_flow():
    # train model
    print('Running training: python train_model.py')
    subprocess.run([sys.executable, 'train_model.py'], env=env, check=True)

    # run main
    print('Running pipeline: python main.py')
    main_proc = subprocess.run([sys.executable, 'main.py'], env=env, capture_output=True, text=True)
    print(main_proc.stdout)
    if main_proc.stderr:
        print('main.py stderr:', main_proc.stderr)

    # run scenario tests
    print('Running scenario tests: python run_scenarios.py')
    subprocess.run([sys.executable, 'run_scenarios.py'], env=env, check=True)

    # run sub-agent evaluation
    print('Running sub-agent evaluation: python evaluation/evaluate_alt_credit.py')
    eval_proc = subprocess.run([sys.executable, 'evaluation/evaluate_alt_credit.py'], env=env, capture_output=True, text=True, check=True)
    print(eval_proc.stdout)

    # collect deliverables outputs
    output_path = 'deliverables/run_full_system_output.json'
    final_output = {
        'main_output': main_proc.stdout.strip(),
        'scenario_results': None,
        'evaluation': eval_proc.stdout.strip(),
        'trace': None
    }

    # load scenario results if exists
    scenario_json = 'deliverables/scenario_test_results.json'
    if os.path.exists(scenario_json):
        with open(scenario_json, 'r') as f:
            final_output['scenario_results'] = json.load(f)

    # get trace from first scenario if available
    if final_output['scenario_results']:
        k = next(iter(final_output['scenario_results'].keys()))
        final_output['trace'] = final_output['scenario_results'][k].get('trace')

    with open(output_path, 'w') as f:
        json.dump(final_output, f, indent=4)

    print(f'Full output available at {output_path}')


def print_ollama_install_hint():
    print("Ollama is not installed. Install with:")
    print("Linux (Codespaces): curl -fsSL https://ollama.com/install.sh | sh")


def clone_repo():
    if not os.path.exists('.git'):
        print('Cloning repository...')
        subprocess.run(['git', 'clone', 'https://github.com/anmoljindal3977-lgtm/CR.git', 'temp_cr'], check=True)
        # Move contents to current dir or cd
        import shutil
        for item in os.listdir('temp_cr'):
            shutil.move(os.path.join('temp_cr', item), '.')
        os.rmdir('temp_cr')
        print('Repository cloned.')


if __name__ == '__main__':
    # clone repo if not already
    clone_repo()

    # ensure requirements
    print('Ensuring requirements are installed')
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)

    from utils.data_loader import ensure_data_available
    # ensure datasets are available
    print('Ensuring datasets are available')
    ensure_data_available()

    # check Ollama
    if not check_command_exists('ollama'):
        print('Installing Ollama...')
        subprocess.run('curl -fsSL https://ollama.com/install.sh | sh', shell=True, check=True)

    # start ollama service
    print('Starting ollama serve...')
    ollama_proc = subprocess.Popen(['ollama', 'serve'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(3)

    # pull model
    print('Pulling model llama3...')
    subprocess.run(['ollama', 'pull', 'llama3'], check=True)

    try:
        run_main_flow()
    except subprocess.CalledProcessError as e:
        print('Error running pipeline:', e)
        if e.stderr:
            print('Stderr:', e.stderr)
        sys.exit(1)
    finally:
        print('Stopping ollama serve...')
        ollama_proc.terminate()
        ollama_proc.wait(timeout=10)
