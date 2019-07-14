# Programming languages appraisal 
***
## Why and What
THis is a training project for better understanding how handling with API services.
It uses api search engine of tow popular sites:  
* [HH.ru](https://api.hh.ru/)  
* [Superjob.ru](https://api.superjob.ru)  


## Installing
Requirements.txt contain all libraries that are needed for executing
Registration is required for the access to Superjob API site
After the application has been registered you will get a secret key
It is needed to create `.env` file with 4 lines:
* Secret_key = Secret_key
* clienr_id = clienr_id
* login = login
* pwd = pwd 

## Usage
The executable module is `looking_for_job_sites.py`
When you run the module it shows two tables with the most popular languages statistics
Statistics obtains for the last 30 days from the most popular Russian sites
Average salary calculates for each programming language  
 

### Advanced usage
If the `popular_language` dictionary  modified it could show another programming language stats 


## Project Goals
The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/modules/)

## License
This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/psergal/bitly/blob/master/license.md) file for details  
