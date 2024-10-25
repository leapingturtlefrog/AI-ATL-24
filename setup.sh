# Optionally run this file with the command 'source ./setup.sh'
# to create and activate a venv for IDE recognition

python3 -m venv venv \
&& source venv/bin/activate \
&& pip install -r requirements.txt \
&& echo "Script successful" || echo "Script unsuccessful"