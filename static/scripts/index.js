setTimeout(() => {
    var alertElement = document.getElementById('alert');
    if (alertElement) {
        alertElement.style.transition = 'opacity 0.5s ease-out';
        alertElement.style.opacity = '0';

        setTimeout(() => {
            if (alertElement.parentNode) {
                alertElement.parentNode.removeChild(alertElement);
            }
        }, 700);
    }
}, 7000);