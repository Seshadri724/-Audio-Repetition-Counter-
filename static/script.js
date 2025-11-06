document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    const setPhraseButton = document.getElementById('set-phrase');
    const startCountingButton = document.getElementById('start-counting');
    const stopCountingButton = document.getElementById('stop-counting');
    const statusMessage = document.getElementById('status-message');
    const referencePhrase = document.getElementById('reference-phrase');
    const targetCountInput = document.getElementById('target-count');
    const similarityThresholdInput = document.getElementById('similarity-threshold');
    const currentCount = document.getElementById('current-count');
    const progressBar = document.getElementById('progress-bar');
    const lastAttempt = document.getElementById('last-attempt');

    setPhraseButton.addEventListener('click', () => {
        socket.emit('set_phrase');
    });

    startCountingButton.addEventListener('click', () => {
        const targetCount = targetCountInput.value;
        const similarityThreshold = similarityThresholdInput.value;
        socket.emit('start_counting', {
            target_count: targetCount,
            similarity_threshold: similarityThreshold
        });
    });

    stopCountingButton.addEventListener('click', () => {
        socket.emit('stop_counting');
    });

    socket.on('update_status', (data) => {
        statusMessage.textContent = data.status;
        referencePhrase.textContent = data.reference_phrase || 'None';
        currentCount.textContent = data.count;
        targetCountInput.value = data.target_count;
        similarityThresholdInput.value = data.similarity_threshold;

        const progress = (data.count / data.target_count) * 100;
        progressBar.style.width = `${progress}%`;

        setPhraseButton.disabled = data.is_counting;
        startCountingButton.disabled = data.is_counting;
        stopCountingButton.disabled = !data.is_counting;
    });

    socket.on('no_match', (data) => {
        lastAttempt.textContent = `"${data.recognized_text}" (no match)`;
    });
});
