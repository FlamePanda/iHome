function getCookie(name) {
    var r = document.cookie.match("\\b" + name  + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

var imageCodeId = "";

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

function generateImageCode() {
	//发送验证码请求
	//获取UUID
	imageCodeId = generateUUID();
	//发送请求
	var url = '/api/v1.0/imageCode/'+imageCodeId;
	$('.image-code img').attr('src',url);
}

function sendSMSCode() {
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    } 
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }
	var url = "/api/v1.0/smsCode/"+imageCodeId
    $.get(url, {'phone_number':mobile, 'picture_code':imageCode}, 
        function(data){
            if (0 != data.errorno) {
                $("#image-code-err span").html(data.errormsg); 
                $("#image-code-err").show();
                generateImageCode();
                $(".phonecode-a").attr("onclick", "sendSMSCode();");
            }   
            else {
                var $time = $(".phonecode-a");
                var duration = 60;
                var intervalid = setInterval(function(){
                    $time.html(duration + "s"); 
                    if(duration === 1){
                        clearInterval(intervalid);
                        $time.html('获取验证码'); 
                        $(".phonecode-a").attr("onclick", "sendSMSCode();");
                    }
                    duration = duration - 1;
                }, 1000, 60); 
            }
    }, 'json'); 
}

$(document).ready(function() {
    generateImageCode();
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });
    $(".form-register").submit(function(e){
        e.preventDefault();
        var mobile = $("#mobile").val();
        var phoneCode = $("#phonecode").val();
        var passwd = $("#password").val();
        var passwd2 = $("#password2").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!phoneCode) {
            $("#phone-code-err span").html("请填写短信验证码！");
            $("#phone-code-err").show();
            return;
        }
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        if (passwd != passwd2) {
            $("#password2-err span").html("两次密码不一致!");
            $("#password2-err").show();
            return;
        }
		//发起ajax请求
		var params = {
			phone_number:mobile,
			sms_code:phoneCode,
			password:passwd,
			ensure_password:passwd2
		};
		var data = JSON.stringify(params);
		var url = "/api/v1.0/users";
		$.ajax({
			url:url,
			type:"post",
			data:data,
			dataType:"json",
			contentType:"application/json",
			headers:{
					"X-CSRFToken":getCookie('csrf_token'),
				},
			success:function(data){
				if("0" == data.errorno){
						location.href='/index.html';
					}else{
						alert(data.errormsg);
					}
				}
		});
    });
})
