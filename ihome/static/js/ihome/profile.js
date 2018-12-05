function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
	//请求用户头像数据和名字数据
	//如没有登录，跳转到首页
    //否者正常显示信息
    //发起ajax请求
    var url = "/api/v1.0/users";
    $.get(url,function(data){
		  if("4101" == data.errorno){
               location.href = "/login.html";
			}
          if("0" == data.errorno){
               $("#user-name").val(data.data.user_name);
               $("#user-avatar").attr('src',data.data.url)
           }else{
				alert(data.errormsg);
                    }   
                 },"json");
	//处理用户上传图片的请求
	$("#form-avatar").submit(function(e){
		e.preventDefault();//阻止浏览器的默认请求
		var url = "/api/v1.0/users/avatar";
		$(this).ajaxSubmit({
			url:url,
			type:'post',
			dataType:"json",
			headers:{
				"X-CSRFToken":getCookie('csrf_token'),
				},
			success:function(data){
			 if("4101" == data.errorno){
               location.href = "/login.html";
			}
				if('0' == data.errorno ){
					//刷新该页面
					//location.reload();
					$('#user-avatar').attr('src',data.data.url);
					}else{
					alert(data.errormsg);
					}
			}
		});
	});
	//处理用户修改名字的请求	
	$("#form-name").submit(function(e){
		e.preventDefault();
		var url = "/api/v1.0/users/name";
		var params = {'name':$("#user-name").val()};
		var data = JSON.stringify(params);
		$.ajax({
			url:url,
			data:data,
			type:"put",
			dataType:"json",
			contentType:"application/json",
			headers:{
				"X-CSRFToken":getCookie("csrf_token"),
			},
			success:function(data){
			 if("4101" == data.errorno){
               location.href = "/login.html";
			}
				if('0' == data.errorno){
						alert(data.errormsg);					
						$("#user-name").val(data.data.name);
					}else{
						alert(data.errormsg);
					}
			}
		});
	
	});
	});
