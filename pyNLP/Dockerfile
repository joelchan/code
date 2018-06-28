FROM python:3.6

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt
RUN python -m spacy download en
RUN pip3 install http://download.pytorch.org/whl/cpu/torch-0.4.0-cp36-cp36m-linux_x86_64.whl 
RUN pip3 install torchvision
COPY server /app/server
COPY textProcessing /app/textProcessing
COPY ./ /app
RUN git clone https://github.com/fastai/fastai.git
RUN pip install -e fastai
ENTRYPOINT [ "python" ]

CMD [ "server/app.py" ]