
  var show_details = function(){
    var gestion = $(this).data('id');
    console.log(gestion);
    $.ajax('/dtracking/view_details/',{
      type: 'POST',
      data: {'id': gestion},
      success: function(data){
        console.log(data);
        var modal = $('#grappelli-modal');
        var indicadores = modal.find(".carousel-indicators").empty();
        var carousel = modal.find(".carousel-inner").empty();
        $.each(data.media, function(key, value){
          var clase = "";
          if (key==0) {
            clase = "active"
          } else {
            clase = ""
          }
          var indicador = '<li data-target="#myCarousel" data-slide-to="'+key+'" class="'+clase+'"></li>'
          var item = '<div class="item '+clase+'"><img class="'+value.variable+'" src="'+value.archivo+'" alt="'+value.variable+'"><div class="container"><div class="carousel-caption"><h1>'+value.variable+'</h1></div></div></div>'
          indicadores.append(indicador);
          carousel.append(item)
        });
        modal.modal('show');
      },
    })
  }
  $(document).on('ready', function(){
    $('.detalle').on('click', show_details);
  });
