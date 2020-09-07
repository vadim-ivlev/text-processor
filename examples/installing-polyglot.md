Installing Polyglot over Anaconda
---------------------------------

```bash
source ~/.bashrc
bash ~/Downloads/Anaconda3-2018.12-Linux-x86_64.sh 
# conda install -c conda-forge pyicu
conda config --add channels conda-forge
conda activate base
conda update conda
conda install pyicu
pip install polyglot
pip install pycld2
pip install Morfessor
conda install -c conda-forge fish
```

Installing Polyglot in an Environment
---------------------------------
```bash
conda create --name py37 python=3.7
conda activate py37
conda install -c conda-forge numpy
conda install -c conda-forge pyicu
pip install pycld2
pip install morfessor
pip install polyglot

# Downloading models
polyglot download LANG:en
polyglot download LANG:ru
```




