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



            // Display the image if available

            const storyImage = document.getElementById('story-image');

            if (data.image) {

                const img = storyImage.querySelector('img');

                img.src = `data:image/png;base64,${data.image}`;

                storyImage.classList.remove('hidden');

                

                // Show the share buttons

                const shareButtons = document.querySelector('.share-buttons');

                shareButtons.classList.remove('hidden');

            } else {

                storyImage.classList.add('hidden');

            }



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



    // Update the URL parameter function to also check for parent window

    function getUrlParameter(name) {

        try {

            // First try to get from current URL

            let value = new URLSearchParams(window.location.search).get(name);

            

            // If not found and we're in an iframe, try to get from parent

            if (!value && window.parent !== window) {

                // Try to get from parent's URL if possible

                value = new URLSearchParams(window.parent.location.search).get(name);

            }

            

            // If still not found, try to get from localStorage

            if (!value) {

                value = localStorage.getItem('auth_token');

            }

            

            console.log('Token found:', value ? 'yes' : 'no'); // Debug log

            return value;

        } catch (e) {

            console.log('Error getting token:', e); // Debug log

            return localStorage.getItem('auth_token');

        }

    }



    // Add function to store token

    function storeToken(token) {

        if (token) {

            localStorage.setItem('auth_token', token);

            console.log('Token stored in localStorage'); // Debug log

        }

    }



    // When page loads, try to get and store token

    const token = getUrlParameter('token');

    if (token) {

        storeToken(token);

    }



    // Update the send story click handler

    const sendStoryBtn = document.querySelector('.story-btn');

    if (sendStoryBtn) {

        sendStoryBtn.addEventListener('click', async function() {

            const storyContent = document.getElementById('story-content').textContent;

            const token = getUrlParameter('token') || localStorage.getItem('auth_token');

            

            console.log('Using token:', token ? 'yes' : 'no'); // Debug log

            

            if (!token) {

                showError('No authentication token available. Please refresh the page.');

                return;

            }



            try {

                const response = await fetch('/send-to-chat', {

                    method: 'POST',

                    headers: {

                        'Content-Type': 'application/json',

                    },

                    body: JSON.stringify({ 

                        story: storyContent,

                        token: token

                    })

                });



                const data = await response.json();



                if (!response.ok) {

                    throw new Error(data.error || 'Failed to send story to chat');

                }



                showSuccess('Story sent to chat successfully! ✨');



            } catch (error) {

                console.error('Error:', error);

                showError(error.message);

            }

        });

    }



    // Add success message function

    function showSuccess(message) {

        const successDiv = document.createElement('div');

        successDiv.className = 'success-message';

        successDiv.textContent = message;

        document.querySelector('.story-container').appendChild(successDiv);

        

        // Remove success message after 3 seconds

        setTimeout(() => {

            successDiv.remove();

        }, 3000);

    }

});
