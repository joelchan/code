# Deploy python graphql /nlp server with docker locally
```bash
git clone git@github.com:matt-erhart/code.git
#install docker and make sure its running in the background
#need powershell not gitbash for windows
cd code/pyNLP
#this puts the built docker image in 'docker land' which you can only access with docker commands.
# increase docker memory to 8gb
docker build -t pynlp:latest . # run again if you change anything (for now)
#takes a while the first time
docker images # see your built images in dockers memory/storage: includes pynlp
docker run -it -p 5000:5000 pynlp #-it interactive, -p port mapping. pynlp name from above
# you should see flask output and an ip like 0.0.0.0:5000
# use -d instead of -it to run in the background
docker ps # to view your running docker containers
# you need info in ps to stop containers running in the background or to attach to a running process
```

# Run the react development server locally
```bash
# download node.js version 8ish: https://nodejs.org/en/ #20180510
# install yarn package manager: https://yarnpkg.com/lang/en/docs/install #like npm but often better for cross os installs
cd xml2react
yarn #no args, will install everything in package.json
# might need to install some missing global packages
yarn start # 'start' command defined in package.json: launches dev server
```

# AWS EC2 
cd ~/.ssh

ssh -i ~/.ssh/id_rsa ubuntu@34.221.165.5 -L8888:localhost:8888 //only need id_rsa once. ip changes.
//now on aws instance
cd fastai
git pull
python -m spacy download en
conda env update #once a month
jupyter notebook



