FROM heroku/miniconda:3

# Grab requirements.txt.
ADD ./app/requirements.txt /tmp/requirements.txt

# Install dependencies
RUN pip install -qr /tmp/requirements.txt

# Add our code
ADD ./app /opt/app/
WORKDIR /opt/app

RUN conda install geopandas

CMD streamlit run "Estadísticas Covid Chile.py"