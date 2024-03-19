# Nobel Prizes by Academic Affiliations 

## Overview

This repository hosts a dataset detailing the academic affiliations of Nobel Prize laureates, exploring the nexus between Nobel laureates and their educational or professional institutions. This endeavor was sparked by curiosity and a passion for understanding the academic roots of excellence.

## Dataset Description

The dataset provides a comprehensive view of the affiliations of Nobel laureates, capturing their connections to academic institutions worldwide. It aims to facilitate a deeper understanding of the educational and professional environments that have nurtured Nobel Prize winners across all categories.

## Data Collection

In order to collect this data, I created a script that scrapes all Nobel Laureates from the Wikipedia list, and then goes to each laureate's wikipedia page to scrape both their alma matters (Bachelors, Masters, PhD) and institutions (colleges where they've worked).  This data is extracted from the "info-box" at the top right of each page, as this box includes only their significant affiliations, rather than places where they might have taught for a couple years.

Because of the extremely high accuracy of Wikipedia, this data is extremely accurate, but there are a few small errors.  One example is the University of Chicago, which officially reports to having 99 laureates, only has 95 in this data set.  One example is Barack Obama, who taught at UChicago for 13 years, however the "Presidential info-box" element does not support academic affiliations so this is not counted in the dataset.  There are small issues like this, but it's important to note that this only happens in special cases and that it only undercounts.

## Using This Dataset

The dataset is available for educational, research, and informational purposes. It offers valuable insights for researchers, educators, and anyone interested in the academic backgrounds of Nobel Prize winners. Users are encouraged to delve into the data to uncover trends, patterns, and noteworthy affiliations.

## Contribution Guidelines

While the dataset is provided as a finalized resource, suggestions for additions or corrections are welcome. If you have verified information that could refine or expand the dataset, please shoot me an email at frishberg@uchicago.edu.

## Acknowledgments

- The Nobel Prize organization, for their role in celebrating global achievements.
- Various data sources, including Wikipedia, for providing accessible information on Nobel laureates.
- The academic institutions themselves, for fostering environments conducive to groundbreaking work.

## Contact Information

For inquiries, suggestions, or further discussion related to the dataset, feel free to send me an email at frishberg@uchicago.edu.
