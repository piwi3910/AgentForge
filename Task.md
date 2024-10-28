We are building a frontend and backend application.
For now we focus on the backend. The backend will be based on flask with a local file db.
The backend will create multiple api's with swagger frontend

the application will need to following api calls.

We will be building an application that will allow users to easily create an Agentic team of AI LLM's

we need to be able to login and register an user with email and pass
we need a profile page to modify a password, and we also need a password reset fucntion 

We need a models fucntion
in this fucntion with need to he option to add api keys for: Openai, Entropic, Openrouter, Ollama and override the default api endpoint (optional) if the user wants this.

When we add our api key, it should test the api key for that scpecific provider and if it is successfull save the key to.
We should then have a function to check all the models available with that provider
We shoudl then be able to tell wich models we want to enable for further use in our application

We should then have a team function.
In here we should be able to define a team by name and what it's function will be.
we always add a project manager to the team and we should be able to select the model to use for the project manager from the enabled models

We should then be able to add multiple agents with different names and functionality and the option to select differnt models from our enabled list.. to make this a true Agentic framework.

Have a look at other agentic frameworks how these agents should interact with eachother

Finally we should be able to have a caht function, where we can select the team we created. and start chatting with the project manager.
We should be able to tell our project manager what we want, and it will delegate tasks to the different agents, and execute what i asked them to do. And give me back the result

The frontend should be able to run on web and mobile. preferably React-native.

The frontend should not have any functionality in it, except for display, all operations and fucntions should be handled by the backend and presneted to the frontedn via api
