document.addEventListener('DOMContentLoaded', function() {
    const customerSelect = document.getElementById('customer-select');
    const customerDetails = document.getElementById('customer-details');
    const displayName = document.getElementById('display-name');
    const displayEmail = document.getElementById('display-email');
    const displayPhone = document.getElementById('display-phone');
    const displayAddress = document.getElementById('display-address');
    
    // Use data attributes from option elements instead of inline Django template logic
    customerSelect.addEventListener('change', function() {
        const selectedId = this.value;
        
        if (selectedId) {
            // Show customer details
            customerDetails.style.display = 'block';
            
            // Get the selected option element
            const selectedOption = this.options[this.selectedIndex];
            
            // Get customer data from data attributes
            displayName.textContent = selectedOption.dataset.name;
            displayEmail.textContent = selectedOption.dataset.email;
            displayPhone.textContent = selectedOption.dataset.phone || 'Not provided';
            displayAddress.textContent = selectedOption.dataset.address;
        } else {
            customerDetails.style.display = 'none';
        }
    });
});