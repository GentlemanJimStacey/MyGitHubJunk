function grabAllData() {
  const SWAPI = "https://swapi.co/api/people/"
  let name = document.getElementById("name").value.toUpperCase();

  //attempts to grab the data
  fetch(SWAPI)
    //waits until response
    .then(response => {
      //once it has response, converts it to json    
      response.json().then(data => {
        //loops through the results, searching for a name that matches
        for (i in data.results) {
          if (data.results[i].name.toUpperCase() === name) {
            grabUserData(data.results[i].homeworld);
            return;
          }
        }
        window.alert("That name doesn't exist!");
      });
    })
    //catches any fetch errors
    .catch(err => {
      console.log('Fetch Error', err);
    });
};
//accepts an API URL for the selected person
function grabUserData(homeWorldURL) {
  fetch(homeWorldURL)
    .then(response => {
      response.json().then(data => {
        document.getElementById("planet").innerHTML = data.name;
        document.getElementById("climate").innerHTML = data.climate;
        document.getElementById("population").innerHTML = data.population;
      });
    })
    //catches any errors
    .catch(err => {
      console.log('Fetch Error', err);
    });
};