document.addEventListener('DOMContentLoaded', () => {
    console.log("Invoice QC Dashboard Loaded");

    // Optional: Add a listener to the file input to show an alert or log
    const fileInput = document.querySelector('input[type="file"]');
    
    if(fileInput) {
        fileInput.addEventListener('change', (e) => {
            const fileCount = e.target.files.length;
            console.log(`${fileCount} files selected.`);
        });
    }
});