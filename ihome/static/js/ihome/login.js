function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    $(".form-login").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
		//发起ajax请求
		var params = {
			phone_number:mobile,
			password:passwd
		};
		var data = JSON.stringify(params);
		var url = "/api/v1.0/sessions";
		$.ajax({
			url:url,
			type:"post",
			data:data,
			contentType:"application/json",
			dataType:"json",
			headers:{
					"X-CSRFToken":getCookie('csrf_token'),
				},
			success:function(data){
				if('0' == data.errorno){
					//用户登录成功
					location.href='/index.html';
				}else{
					//失败，弹出消息
					alert(data.errormsg);
				}	
			}
		});
    });
})
