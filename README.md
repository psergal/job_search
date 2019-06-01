# Space Instagram
***
## Why and What
THis is a training project for better understanding how handling with API services.
It grabs photo images from two popular web-sites:  
* [SpaceX](https://github.com/r-spacex/SpaceX-API)  
* [HubbleSite](http://hubblesite.org/api/documentation)  

There is no registration require for the API usage. 

## Installing
The code executes by __Python 3.7__.   
Then use __pip__ for installing depended libraries:  
`pip install -r requirements.txt`
It is better to use separate account for [Instagram](https://www.instagram.com)
When the Instagram account is created and activated you should save credentials
into `.env` file. Insta_post module reads from the environments by names:
+ inst_name
+ inst_pass   

## Usage
There are three independent modules comprise project:
+ `fetch_space.py`
+ `fetch_hubble.py`
+ `insta_post.py`
### Easy usage  
They can be run in the console without args.
`python fetch_spacex.py` downloads pictures random or latest picture, depending on variables mode.  
`python fetch_hubble.py` downloads pictures by picture_id
`python insta_post.py` uploads pictures to the Instagram.
All modules use the same dictionary __images__ to store and uploading.
### Advanced usage
Every module can takes args. You can pass
* `--img_name` image file name for the storage
* `--img_id` Id for remote image file for fetch_hubble call
* `--flight_mode` latest or random flight for fetch_spacex call
* `--img_dir` folder for the storage of downloading files and uploading
 to the Instagram account 
 
Help about args might be showed with `-h` key arg   

## Project Goals
The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/modules/)

## License
This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/psergal/bitly/blob/master/license.md) file for details  
