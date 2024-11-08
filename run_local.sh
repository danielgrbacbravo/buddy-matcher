
# check what operating system we are on
unameOut="$(uname -s)"
echo "Operating system: $unameOut"
function setup_venv(){
  echo "Setting up virtual environment"
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
}
if [[ $unameOut == "Darwin" ]]; then
  brew update || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  brew install python3
  [[ -d ".venv" ]] && source .venv/bin/activate || setup_venv
  pip install --upgrade pip || python3 -m ensurepip
  echo "Successfully installed python3 and virtual environment"
  python src/main.py && deactivate
fi
if [[ $unameOut == "Linux" ]]; then
  sudo apt update
  sudo apt install python3
  [[ -d ".venv" ]] && source .venv/bin/activate || setup_venv
  pip install --upgrade pip || python3 -m ensurepip
  echo "Successfully installed python3 and virtual environment"
  python src/main.py && deactivate
fi
