document.addEventListener('DOMContentLoaded', function () {
    const maxStudentsInput = document.getElementById('id_max_students');
    if (!maxStudentsInput) return;

    // Create Default button
    const defaultBtn = document.createElement('button');
    defaultBtn.type = 'button';
    defaultBtn.textContent = 'Default';
    defaultBtn.className = 'default-btn';
    defaultBtn.style.marginLeft = '10px';

    // Create Clear button
    const clearBtn = document.createElement('button');
    clearBtn.type = 'button';
    clearBtn.textContent = 'Clear Default';
    clearBtn.className = 'clear-btn';
    clearBtn.style.marginLeft = '10px';
    clearBtn.style.display = 'none';

    // Create info text
    const infoText = document.createElement('span');
    infoText.className = 'default-info';
    infoText.style.marginLeft = '10px';
    infoText.style.color = '#28a745';
    infoText.style.fontWeight = 'bold';
    infoText.style.display = 'none';

    // Insert elements after input
    maxStudentsInput.parentNode.insertBefore(defaultBtn, maxStudentsInput.nextSibling);
    maxStudentsInput.parentNode.insertBefore(clearBtn, defaultBtn.nextSibling);
    maxStudentsInput.parentNode.insertBefore(infoText, clearBtn.nextSibling);

    // Helper to activate default
    function activateDefault() {
        maxStudentsInput.value = '';
        maxStudentsInput.placeholder = 'Default capacity is active';
        maxStudentsInput.style.backgroundColor = '#e6ffe6';
        maxStudentsInput.style.borderColor = '#28a745';
        infoText.textContent = '✓ Default capacity is active';
        infoText.style.display = '';
        defaultBtn.textContent = '✓ Default Selected';
        defaultBtn.style.backgroundColor = '#28a745';
        defaultBtn.style.color = '#fff';
        clearBtn.style.display = '';
        // Set a hidden field or data attribute for form submission
        maxStudentsInput.setAttribute('data-default-active', 'true');
    }

    // Helper to deactivate default
    function deactivateDefault() {
        maxStudentsInput.placeholder = '';
        maxStudentsInput.style.backgroundColor = '';
        maxStudentsInput.style.borderColor = '';
        infoText.textContent = '';
        infoText.style.display = 'none';
        defaultBtn.textContent = 'Default';
        defaultBtn.style.backgroundColor = '';
        defaultBtn.style.color = '';
        clearBtn.style.display = 'none';
        maxStudentsInput.removeAttribute('data-default-active');
    }

    // Default button click
    defaultBtn.addEventListener('click', function () {
        activateDefault();
    });

    // Clear button click
    clearBtn.addEventListener('click', function () {
        deactivateDefault();
        maxStudentsInput.value = '';
    });

    // If user types, clear default state
    maxStudentsInput.addEventListener('input', function () {
        if (maxStudentsInput.getAttribute('data-default-active')) {
            deactivateDefault();
        }
    });

    // On form submit, set value to 96 if default is active
    const form = maxStudentsInput.form;
    if (form) {
        form.addEventListener('submit', function () {
            if (maxStudentsInput.getAttribute('data-default-active')) {
                maxStudentsInput.value = 96;
            }
        });
    }

    // If editing and value is 96, show as default
    if (maxStudentsInput.value === '96') {
        activateDefault();
    }
});