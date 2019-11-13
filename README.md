# chord_recognition

## To deploy the application
First, locally, run the command:
* `make build tag=<tag>`: This will build the docker and upload it to the ECR in amazon
* scp the update_app.sh file to the server

In AWS:
* Create an EC2 instance
* Create a security group with the port 80 open
* Attach the security group to the instance

Then, in the server install the following:
* Install docker
* Install nginx
* Install awscli
* Populate the `~/.aws/configure` and `~/.aws/config` files
* `sudo groupadd docker`
* `sudo usermod -aG docker $USER`
* `sudo mkdir /var/log/nginx/`
* `sudo mkdir /chord-recognition/db/`
* `sudo chmod +x update_app.sh`
* `sudo mv update_app.sh /usr/local/bin/`
* `update_app.sh <tag>`
* copy the `chord-recognition.conf` to `/etc/nginx/sites-available/`
* `sudo ln -s /etc/nginx/sites-available/chord-recognition.conf /etc/nginx/sites-enabled/`
* `sudo systemctl start nginx`

