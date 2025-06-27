// Animation
lottie.loadAnimation({
  container: document.getElementById('animation'),
  renderer: 'svg',
  loop: true,
  autoplay: true,
  path: 'animation.json'
});

// Gestion des interactions utilisateur
const uploadArea = document.getElementById('uploadArea');
const audioFileInput = document.getElementById('audioFile');
const convertBtn = document.getElementById('convertBtn');
const resultDiv = document.getElementById('result');
const loadingDiv = document.getElementById('loading');
const downloadLink = document.getElementById('downloadLink');
const fileNameSpan = document.getElementById('fileName');

// Gestion du drag and drop
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
        fileNameSpan.innerHTML = `<i class="fas fa-check mr-1"></i> Fichier sélectionné : ${file.name}`;
    } else {
        alert('Veuillez déposer un fichier audio valide.');
    }
});

// Affichage du nom du fichier sélectionné
audioFileInput.addEventListener('change', () => {
    const file = audioFileInput.files[0];
    if (file) {
        fileNameSpan.innerHTML = `<i class="fas fa-check mr-1"></i> Fichier sélectionné : ${file.name}`;
    }
});

// Gestion de la conversion
convertBtn.addEventListener('click', async () => {
    const file = audioFileInput.files[0];
    if (!file) {
        alert('Veuillez sélectionner un fichier audio.');
        return;
    }

    const format = document.querySelector('input[name="output"]:checked').value;
    const formData = new FormData();
    formData.append('audio', file);
    formData.append('format', format);

    // Afficher l'indicateur de chargement
    resultDiv.classList.remove('hidden');
    loadingDiv.classList.remove('hidden');
    downloadLink.classList.add('hidden');

    try {
        // Appel simulé à l'API backend (à remplacer par une vraie URL)
        const response = await fetch('/convert', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Échec de la conversion');
        }

        const data = await response.json();
        downloadLink.href = data.url;
        downloadLink.textContent = `Télécharger votre fichier ${format.toUpperCase()}`;
        downloadLink.classList.remove('hidden');
        loadingDiv.classList.add('hidden');

        // Animation GSAP pour le lien de téléchargement
        gsap.from(downloadLink, { opacity: 0, y: 20, duration: 0.5 });
    } catch (error) {
        console.error(error);
        alert('Une erreur est survenue lors de la conversion.');
        loadingDiv.classList.add('hidden');
    }
});

// Animation GSAP pour l'entrée du titre
gsap.from('h1', { y: -50, opacity: 0, duration: 1, ease: 'power2.out' });