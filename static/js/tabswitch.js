// tabswitch.js
function setupToggleSlider(tabContainerId, sliderId) {
    const tabContainer = document.getElementById(tabContainerId);
    const slider = document.getElementById(sliderId);

    if (!tabContainer || !slider) {
        console.error(`Could not find elements for slider setup: ${tabContainerId}, ${sliderId}`);
        return;
    }

    function moveSlider(targetButton) {
        if (!targetButton) return;

        const targetLeft = targetButton.offsetLeft;
        const targetWidth = targetButton.offsetWidth;

        
        slider.style.left = targetLeft + 'px';
        slider.style.width = targetWidth + 'px';
    }

    const activeTabButton = tabContainer.querySelector('.nav-link.active');
    if (activeTabButton) {
        
        setTimeout(() => moveSlider(activeTabButton), 0);  
        moveSlider(activeTabButton); 
    }

    tabContainer.addEventListener('show.bs.tab', (event) => {
        moveSlider(event.target); 
    });

    window.addEventListener('resize', () => {
        const currentActiveButton = tabContainer.querySelector('.nav-link.active');
        if (currentActiveButton) {
            moveSlider(currentActiveButton);
        }
    });
}

