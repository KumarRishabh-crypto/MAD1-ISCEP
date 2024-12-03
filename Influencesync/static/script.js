const pieChart = document.getElementById('pieChart').getContext('2d');
const barChart = document.getElementById('barChart').getContext('2d');

var countinflu=document.getElementById('influ');
var countspon=document.getElementById('spon');

countinflu=Number(countinflu.textContent)
countspon=Number(countspon.textContent)

const myPieChart = new Chart(pieChart, {
    type: 'doughnut',
    data: {
        labels: ['Influencers', 'Sponsors'],
        datasets: [{
            data: [countinflu,countspon],
            backgroundColor: ['#36A2EB', '#FFCE56'],
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
    }
});

var flag = document.getElementById('flag')
var total = document.getElementById('total')
var camp = document.getElementById('camp')
var active_camp = document.getElementById('active_camp')

var flag = Number(flag.textContent)
var total = Number(total.textContent)
var camp = Number(camp.textContent)
var active_camp = Number(active_camp.textContent)

const myBarChart = new Chart(barChart, {
    type: 'bar',
    data: {
        labels: ['Campaigns', 'Users'],
        datasets: [{
            label: 'Total',
            data: [camp, total],
            backgroundColor: '#36A2EB',
        }, {
            label: 'Flagged',
            data: [0, flag],
            backgroundColor: '#FFCE56',
        },
        {
            label: 'Active Campaign',
            data: [active_camp],
            backgroundColor: '#22DD22',
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
            }
        }
    }
});
