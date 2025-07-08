// Lottie animation
lottie.loadAnimation({
  container: document.getElementById('animation'),
  renderer: 'svg',
  loop: true,
  autoplay: true,
  path: 'animation.json'
});

// Element references
const uploadArea = document.getElementById('uploadArea');
const audioFileInput = document.getElementById('audioFile');
const convertBtn = document.getElementById('convertBtn');
const convertText = document.getElementById('convertText');
const convertSpinner = document.getElementById('convertSpinner');
const fileNameSpan = document.getElementById('fileName');

// Drag & drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('audio/')) {
        audioFileInput.files = e.dataTransfer.files;
        fileNameSpan.innerHTML = `<i class="fas fa-check mr-1"></i> Selected file: ${file.name}`;
    } else {
        alert('Please drop a valid audio file.');
    }
});

// Display selected file name
audioFileInput.addEventListener('change', () => {
    const file = audioFileInput.files[0];
    if (file) {
        fileNameSpan.innerHTML = `<i class="fas fa-check mr-1"></i> Selected file: ${file.name}`;
    }
});

// Conversion
convertBtn.addEventListener('click', async () => {
    const file = audioFileInput.files[0];
    if (!file) {
        alert('Please select an audio file.');
        return;
    }

    const format = document.querySelector('input[name="output"]:checked').value;
    const formData = new FormData();
    formData.append('audio', file);
    formData.append('format', format);

    // Show spinner and hide button text
    convertText.classList.add('hidden');
    convertSpinner.classList.remove('hidden');

    try {
        const response = await fetch('/convert', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Conversion failed');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `conversion.${format}`;
        a.click();
        window.URL.revokeObjectURL(url);

    } catch (error) {
        console.error(error);
        alert('An error occurred during conversion.');
    } finally {
        // Restore button text and hide spinner
        convertText.classList.remove('hidden');
        convertSpinner.classList.add('hidden');
    }
});

// GSAP animation
gsap.from('h1', { y: -50, opacity: 0, duration: 1, ease: 'power2.out' });
