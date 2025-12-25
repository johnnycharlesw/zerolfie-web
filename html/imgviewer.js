  (function(){
    try {
      const params = new URLSearchParams(location.search);
      const src = params.get('src') || '';
      const img = document.getElementById('image');
      if (src && img) {
        img.src = src;
        document.title = src.split('/').pop() || 'Image';
      }
    } catch(e) {}
  })();