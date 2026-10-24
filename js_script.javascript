document.addEventListener('DOMContentLoaded', () => {
    fetchTicketsData();
});

function fetchTicketsData() {
    fetch('http://localhost:8080/api/tickets', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer your_access_token' // Substitua pelo token de acesso real
        }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('total-tickets').textContent = data.total;
        document.getElementById('pending-tickets').textContent = data.pending;
        document.getElementById('resolved-tickets').textContent = data.resolved;
        document.getElementById('pending-tickets-status').textContent = data.pending;
    })
    .catch(error => {
        console.error('Erro ao buscar dados de tickets:', error);
    });
}
