// Add this at the top
console.log('Reservation.js loaded');

document.addEventListener('DOMContentLoaded', function() {
    // Debugging message to check if the script is loaded
    console.log('DOM loaded - initializing reservation form');
    
    const form = document.getElementById('reservation-form');
    if (!form) {
        console.error('Reservation form not found!');
        return;
    }
    
    // Get form elements
    const checkInInput = document.getElementById('check-in');
    const checkOutInput = document.getElementById('check-out');
    const guestsInput = document.getElementById('guests');
    const priceDisplay = document.getElementById('price-display');
    const totalDisplay = document.getElementById('total-price');
    const cleaningFeeDisplay = document.getElementById('cleaning-fee');
    const submitButton = document.getElementById('reserve-button');

    // Customer information
    const customerSelect = document.getElementById('customer-select');
    
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
        // Check if the dates are valid and the cottage is free for reservation
        fetch(`/reservations/check-availability/?cottage_id=${cottageId}&start_date=${startDate}&end_date=${endDate}`)
            .then(response => response.json())
            .then(data => {
                if (data.available) {
                    // Update pricing info
                    priceDisplay.textContent = `€${data.base_price_total} (€${basePriceValue} × ${data.nights} nights)`;
                    // A null check before updating cleaningFeeDisplay
                    if (cleaningFeeDisplay) {
                        cleaningFeeDisplay.textContent = `€${data.cleaning_fee}`;
                    }
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
        console.log('Form submitted');
        
        // Check if user is authenticated via dataset attribute
        if (form.dataset.userAuthenticated === 'True') {
            const formData = new FormData();
            formData.append('cottage_id', cottageId);
            formData.append('start_date', checkInInput.value);
            formData.append('end_date', checkOutInput.value);
            formData.append('guests', guestsInput.value);
            // Customer information
            formData.append('customer_id', customerSelect.value);
            
            // Get CSRF token from cookie
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch('/reservations/create-ajax/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                },
                body: formData
            })
            .then(response => {
                console.log('Response received:', response.status);
                return response.json();
            })
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
    
});