
window.addEventListener('load', function () {
    var overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.add('hidden');
});

document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function () {
        var overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.classList.remove('hidden');
    });
});
