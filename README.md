# canvas_research
ssh into server (if need to query db)

0. To get started:
conda env create -f environment.yml

1. to activate conda virtual env:
conda activate canvas_data (if this doesn't work you might need to execute (3))

2. freezing python packages (if installed new dependency for project):
conda env export -n canvas_data | grep -v "^prefix: " > environment.yml

3. if environment name mirrors local file path run: 
conda config --set env_prompt '({name}) '

4. to run file:
python <file path relative to git repo>