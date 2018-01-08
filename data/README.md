# *Web Scraping for MovieNet*

```
usage: python scrape.py [-h] MODE [MODE ...] [-p PATH]

Web Scraping for MovieNet

positional arguments:
  MODE                  choose from 'actors', 'charts', 'cinematographers',
                        'composers', 'directors', 'distributors',
                        'franchises', 'index', 'keywords', 'movies',
                        'producers', 'production_companies',
                        'production_countries', 'screenwriters'

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  specify the output directory (default: '.')

Copyright © 2018 Daryl Kang
```

### **▸ _Master Data_**
- **Movies** (*Source: [The Numbers](https://www.the-numbers.com)*)
  * [`movies.csv`]()

### **▸ _Metadata_**
- **Index of Movies** (*Source: [The Numbers](https://www.the-numbers.com)*)
  * [`index.csv`]()
- **Theatrical Box Office Charts** (*Source: [The Numbers](https://www.the-numbers.com)*)
  * [`daily.csv`]()
  * [`weekend.csv`]()
  * [`weekly.csv`]()

### **▸ _Reference Data_**
- **Cast & Crew** (*Source: [Box Office Mojo](http://www.boxofficemojo.com)*)
  * [`actors.csv`]()
  * [`directors.csv`]()
  * [`producers.csv`]()
  * [`screenwriters.csv`]()
  * [`cinematographers.csv`]()
  * [`composers.csv`]()
- **Other Attributes** (*Source: [The Numbers](https://www.the-numbers.com)*)
  * [`distributors.csv`]()
  * [`franchises.csv`]()
  * [`keywords.csv`]()
  * [`production_companies.csv`]()
  * [`production_countries.csv`]()
  
