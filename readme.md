# Manu Le Menu

### What is this ?

This project is a ***chatbot** that recommends restaurants over facebook messenger. I made it for restaurants in Paris only for now.

### How it works ?

It uses **Python** and **Django** for setting up a small webserver that communicates with facebook messenger throught a webhook. **To use it you will need to provide your own facebook api token**.

This was a good way for me to get familiarities with webhooks as well as to sharpen my skills with Django. 

Technically, I find the most intuitive way to think about how it works is a simple state machine : the bot goes from one state to another as it finds substrings (such as neightborhood or type of food) in the user inputs. Then it answers the appropriate way and keeps track of all the information the user gave, until it has enought to conclude on the most reliable piece of advice.

I also implemented a few fancy features such as an efficient implementation of **orthographic correction** (with levhenstein automatas)

### Why are there no db ???

I don't own the data at all, to be honest they were scrapped from yelp. Hence if you want to run it on your own, well you'll need to scrape them too. It's pretty easy to do, just make sure to scrape intelligently and not to be a bad guy !

All that's available are the categories.txt and neightborhood.txt. They hold lists of words that are currently used for matching words when they need orthographic correction. It's not the most reliable way to do that but it's ok regarding the small size of the datas.

### Check out my portfolio !

I might be looking for a job or an internship ! if you like this repo, don't forget to check me out on https://elkael.com 