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

* `SJ_SECRET_KEY = Secret_key`
* `SJ_CLIENT_ID = clienr_id`
* `SJ_LOGIN = login`
* `SJ_PWD = pwd` 

## Usage
The executable module is `looking_for_job_sites.py`  
There are no any parameters for the execution. 
They are declared in the module:  
* Region - Moscow
* Period looking for - last month
* Job - Developer
* Popular language are gotten from the last Github review

just type `python looking_for_job_sites.py`

It should output two tables with requested stats.  
It will look like the followed example:

![output example](doc/salary_report.jpg)


When you run the module it shows two tables with the most popular languages statistics  
Statistics obtains for the last 30 days from the most popular Russian sites mentioned above  
Average salary calculates for each programming language that are declared in dict `pop_language` 
 

### Advanced usage
If the `popular_language` dictionary  modified it could show another programming language stats 


## Project Goals
The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/modules/)

## License
This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/psergal/bitly/blob/master/license.md) file for details  
