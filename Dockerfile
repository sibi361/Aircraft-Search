FROM python:3.9-slim

RUN /usr/sbin/useradd --no-create-home -u 1000 user

COPY requirements_docker.txt .

RUN pip install --no-cache-dir -r requirements_docker.txt -f https://download.pytorch.org/whl/torch_stable.html

COPY streamlit_web_interface.py .

CMD streamlit run streamlit_web_interface.py
