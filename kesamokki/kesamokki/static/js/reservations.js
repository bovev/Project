document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('reservation-form');
    const checkInInput = document.getElementById('check-in');
    const checkOutInput = document.getElementById('check-out');
    const guestsInput = document.getElementById('guests');
    const priceDisplay = document.getElementById('price-display');
    const totalDisplay = document.getElementById('total-price');
    const cleaningFeeDisplay = document.getElementById('cleaning-fee');
    const submitButton = document.getElementById('reserve-button');
    
    // Get data from the form's data attributes
    const cottageId = form.dataset.cottageId;
    const basePriceValue = form.dataset.basePrice;
    const loginUrl = form.dataset.loginUrl;
    
    // Set minimum dates
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const tomorrowStr = tomorrow.toISOString().split('T')[0];
    checkInInput.min = tomorrowStr;
    
    // When check-in date changes, update check-out minimum date
    checkInInput.addEventListener('change', function() {
        const checkInDate = new Date(this.value);
        const minCheckOutDate = new Date(checkInDate);
        minCheckOutDate.setDate(checkInDate.getDate() + 1);
        checkOutInput.min = minCheckOutDate.toISOString().split('T')[0];
        
        // If check-out date is before new min, update it
        if (new Date(checkOutInput.value) < minCheckOutDate) {
            checkOutInput.value = minCheckOutDate.toISOString().split('T')[0];
        }
        
        checkAvailability();
    });
    
    // When check-out date changes, update pricing
    checkOutInput.addEventListener('change', checkAvailability);
    
    function checkAvailability() {
        if (!checkInInput.value || !checkOutInput.value) return;
        
        const startDate = checkInInput.value;
        const endDate = checkOutInput.value;
        
        fetch(`/reservations/check-availability/?cottage_id=${cottageId}&start_date=${startDate}&end_date=${endDate}`)
            .then(response => response.json())
            .then(data => {
                if (data.available) {
                    // Update pricing info
                    priceDisplay.textContent = `€${data.base_price_total} (€${basePriceValue} × ${data.nights} nights)`;
                    cleaningFeeDisplay.textContent = `€${data.cleaning_fee}`;
                    totalDisplay.textContent = `€${data.total_price}`;
                    
                    // Enable booking button
                    submitButton.disabled = false;
                } else {
                    // Show not available message
                    priceDisplay.textContent = `Not available for selected dates`;
                    totalDisplay.textContent = `N/A`;
                    
                    // Disable booking button
                    submitButton.disabled = true;
                }
            });
    }
    
    // Handle form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Check if user is authenticated via dataset attribute
        if (form.dataset.userAuthenticated === 'True') {
            const formData = new FormData();
            formData.append('cottage_id', cottageId);
            formData.append('start_date', checkInInput.value);
            formData.append('end_date', checkOutInput.value);
            formData.append('guests', guestsInput.value);
            
            // Get CSRF token from cookie
            const csrftoken = getCookie('csrftoken');
            
            fetch('/reservations/create-ajax/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Redirect to reservation detail page
                    window.location.href = data.redirect_url;
                } else {
                    alert(`Error: ${data.error}`);
                }
            });
        } else {
            // Redirect to login page
            window.location.href = `${loginUrl}?next=${encodeURIComponent(window.location.pathname)}`;
        }
    });
    
    // Initialize price display
    if (checkInInput.value && checkOutInput.value) {
        checkAvailability();
    }
    
    // Function to get CSRF token from cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});