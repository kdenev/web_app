// Define the updateData function
function updateData() {
    var myForm = document.forms.form1;
    // Make an AJAX request to the Flask server
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/update', true);
    xhr.onload = function () {
        if (xhr.status === 200) {
            // Update the data on the web page
            var dataContainer = document.getElementById('data-container');
            dataContainer.innerHTML = xhr.responseText;
            console.log(xhr.responseText)
        }
    };
    xhr.onerror = function () {
        console.log('Error!');
    };
    xhr.send(new FormData(myForm));
}

// Define the makeChart function
function makeChart(chart_df) {
    const ctx = document.getElementById('chart');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chart_df.map(row => row.name),
            datasets: [{
                label: '# of Votes',
                data: chart_df.map(row => row.value),
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    })
        ;
}