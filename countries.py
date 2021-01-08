from datapackage import Package

def load_countryList (self):
    print('Country list import started')
    package = Package('https://datahub.io/core/country-list/datapackage.json')
    countries = []
    for resource in package.resources:
        if resource.descriptor['datahub']['type'] == 'derived/csv':
            countries = resource.read()
            return countries
