// Scroll to story section from home page
$(".page-scroll").on("click", function(e) {
    e.preventDefault();
    var section = $(this).attr("href");
    $("html, body").animate({
        scrollTop: $(section).offset().top
    }, 1250);
});

$("#time-slider").on("change", function(e) {
    e.preventDefault();
    var value = $(this).val();
    $("#time-slider").val(value);
});

var intervalIds = [];

// Move slider when play is pressed
$("#play").click(function(e) {
    e.preventDefault();
    clearIntervals(intervalIds)
    intervalIds.push(
        iterateSlider(1550, 2016)
    );
});

// Reset slider when rewind is pressed
$("#rewind").click(function(e) {
    e.preventDefault()
    clearIntervals(intervalIds)
    var value = $("#time-slider").val();
    var intVal = Math.floor(value) - 1;
    if (intVal <= 1600) {
        animateRewind(intVal, "1550")
    }
    else if (intVal <= 1700) {
        animateRewind(intVal, "1600")
    }
    else if (intVal <= 1800) {
        animateRewind(intVal, "1700")
    }
    else if (intVal <= 1900) {
        animateRewind(intVal, "1800")
    }
    else if (intVal <= 2000) {
        animateRewind(intVal, "1900")
    }
    else {
        animateRewind(intVal, "2000")
    };
});

$("#rewind").dblclick(function(e) {
    e.preventDefault()
    clearIntervals(intervalIds)
    intervalIds.push (
        iterateSlider(1550, 2016, add=false)
    )
});

$("#pause").click(function(e) {
    clearIntervals(intervalIds);
});

$("#rewind").mousedown(function(e) {
    e.preventDefault();
    intervalIds.push(
        iterateSlider(1550, 2016, add=false)
    );
}).bind('mouseup mouseleave', function() {
    clearIntervals(intervalIds)
});

$("#stop").click(function(e) {
    e.preventDefault();
    clearIntervals(intervalIds)
    $("#time-slider").val("1550")
});

function clearIntervals(obj) {
    obj.forEach(function(element) {
        clearInterval(element);
    });
}

function animateRewind(intVal, valueToSet) {
    var val = {"value": valueToSet};
    var distance = intVal - Math.floor(valueToSet);
    $("#time-slider").animate(val, distance * 5, 'linear');
}

function iterateSlider(min, max, add=true) {
    id = setInterval(function() {
        var value = $("#time-slider").val();
        if (add === true) {
            var intVal = Math.floor(value) + 1;
        }
        else {
            var intVal = Math.floor(value) - 1
        }

        if (intVal >= max) {
            intVal = String(max);
            clearIntervals(intervalIds);
        }
        else if (intVal <= min) {
            intVal = String(min);
            clearIntervals(intervalIds);
        };
        $("#time-slider").val(String(intVal));
    }, 10);
    return id
}

function outputUpdate(vol) {
  if (vol > 2016) {
      vol = 2016;
  }
  else if (vol < 1550) {
      vol = 1550;
  };
  $("#volume").val(vol)
}
