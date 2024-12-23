document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById('generate-btn');
    const descriptionInput = document.getElementById('turtle-description');
    const loadingDiv = document.getElementById('loading');
    const errorMessage = document.getElementById('error-message');
    const currentStory = document.getElementById('current-story');
    const storyContent = document.getElementById('story-content');
    const storyHistory = document.getElementById('story-history');

    // Ensure loading state is hidden initially
    loadingDiv.classList.add('hidden');

    // Clear any existing stories and errors
    errorMessage.classList.add('hidden');
    currentStory.classList.add('hidden');

    generateBtn.addEventListener('click', async function() {
        const description = descriptionInput.value.trim();
        
        if (!description) {
            showError('Please share a description of your sea turtle! 🐢');
            return;
        }

        // Reset states before generation
        currentStory.classList.add('hidden');
        errorMessage.classList.add('hidden');
        
        // Show loading state
        loadingDiv.classList.remove('hidden');
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<span>Generating... 🌊</span>';

        try {
            const response = await fetch('/generate-story', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ description: description })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to generate story');
            }

            // Display the new story
            storyContent.textContent = '';
            currentStory.classList.remove('hidden');
            typeWriter(data.story, storyContent);

            // Update history
            updateHistory(data.history);

        } catch (error) {
            showError(error.message);
        } finally {
            // Always hide loading state and reset button
            loadingDiv.classList.add('hidden');
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<span>✨ Create Magical Story ✨</span>';
        }
    });

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
        errorMessage.style.animation = 'none';
        errorMessage.offsetHeight; // Trigger reflow
        errorMessage.style.animation = 'shake 0.5s ease-in-out';
    }

    function updateHistory(history) {
        storyHistory.innerHTML = '';
        history.forEach((entry, index) => {
            const div = document.createElement('div');
            div.className = 'history-entry';
            div.style.animationDelay = `${index * 0.1}s`;
            div.innerHTML = `
                <p class="timestamp">📅 ${entry.timestamp}</p>
                <p class="description">🐢 <strong>The Turtle:</strong> ${entry.description}</p>
                <p class="story">📖 ${entry.story}</p>
            `;
            storyHistory.appendChild(div);
        });
    }

    function typeWriter(text, element, speed = 30) {
        let i = 0;
        element.textContent = ''; // Clear any existing text
        function type() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        }
        type();
    }
});