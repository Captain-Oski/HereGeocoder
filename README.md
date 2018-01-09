# HereGeocoder<br />
Here Geocoder python scripts<br />

How to : <br />

In the same folder : <br />

input.csv must contain the specific "address" column <br />
  Could be any type of adresses, but best practice would be <br />
  street# streetName postalCode city country<br />
    or <br />
  6 digit postal code (for canada)<br />
  <br />
output.csv will contains lot of useful informations such as :<br />
    <br />
            'formatted_address' : The formated address provided in input<br />
            'latitude' : The latitude of the formatted address<br />
            'longitude' : The longitude of the formatted address<br />
            'relevance' : The accuracy of the provided information (scale 0(null) to 1(perfect geocoding))<br />
            'MatchLevel' : The qualitative accuracy of the geographic reference<br />
            'MatchType' : The type of address that has been submited<br />

  See the Here geocoder documentation here for all details about the results informations provided <br />
 https://developer.here.com/documentation/geocoder/<br />

 <br/><a href="https://ibb.co/daA8E6"><img src="https://preview.ibb.co/irXc7R/full.png" alt="full" border="0"></a>
