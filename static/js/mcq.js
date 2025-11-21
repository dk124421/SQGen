document.addEventListener('DOMContentLoaded', function () {
    const submitBtn = document.getElementById('submit-test-btn');
    const restartBtn = document.getElementById('restart-test-btn');

    if (submitBtn) {
        submitBtn.addEventListener('click', function () {
            const mcqCards = document.querySelectorAll('.mcq-card');
            let score = 0;
            let total = mcqCards.length;

            mcqCards.forEach((card, index) => {
                const questionNumber = index + 1;
                // Get the input for the current question that is checked
                const selectedOption = card.querySelector(`input[name="question_${questionNumber}"]:checked`);
                const correctAnswer = card.getAttribute('data-correct-answer');
                const explanation = card.getAttribute('data-explanation');
                const feedbackContainer = card.querySelector('.feedback-container');
                const optionLabels = card.querySelectorAll('.option-label');
                
                // Disable all options after submission
                card.querySelectorAll('.option-input').forEach(input => input.disabled = true);

                let userAnsweredCorrectly = false;

                if (selectedOption) {
                    const userAnswer = selectedOption.value;
                    if (userAnswer === correctAnswer) {
                        score++;
                        userAnsweredCorrectly = true;
                        feedbackContainer.className = 'feedback-container correct';
                        feedbackContainer.innerHTML = `✅ <p><strong>Correct!</strong> ${explanation}</p>`;
                    } else {
                        feedbackContainer.className = 'feedback-container incorrect';
                        feedbackContainer.innerHTML = `❌ <p><strong>Incorrect.</strong> The correct answer is <strong>${correctAnswer}</strong>. ${explanation}</p>`;
                    }
                } else {
                    // No answer was selected
                    feedbackContainer.className = 'feedback-container incorrect';
                    feedbackContainer.innerHTML = `⚠️ <p><strong>Not Answered.</strong> The correct answer is <strong>${correctAnswer}</strong>. ${explanation}</p>`;
                }
                
                // Highlight the correct answer for all cases
                optionLabels.forEach(label => {
                    const input = label.querySelector('.option-input');
                    if (input.value === correctAnswer) {
                        label.classList.add('correct-highlight');
                    } else if (input.checked && !userAnsweredCorrectly) {
                        label.classList.add('incorrect-highlight');
                    }
                });
                
                feedbackContainer.style.display = 'block';
            });
            
            // --- Final Score Display Logic ---
           
        });
    }

    if (restartBtn) {
        restartBtn.addEventListener('click', function() {
            window.location.href = '/mcq'; 
        });
    }
    

});