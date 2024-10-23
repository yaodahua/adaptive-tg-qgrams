Page objects for the pagekit application.

### Run the application

Execute the Bash script to initialize the Docker image containing the web application:

```commandline
docker compose up -d
```

The application shall run at the address:

`http://localhost:3000/pagekit/index.php/admin/login`

### Admin Credentials

username: `admin`

password: `asdfghjkl123`

### Stop application and remove container

In order to remove the container type `docker compose down`. The command will stop and remove the appropriate containers.
