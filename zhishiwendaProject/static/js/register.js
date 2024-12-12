function bindEmailCaptchaClick(){
   $("#captcha-btn").click(function (event) {
     var $this=$(this);//代表当前按钮的jquery对象
     event.preventDefault();//阻止默认的事件，比如提交表单内容到服务器
     var email=$("#exampleInputEmail1").val();
     var countdown=60;//做倒计时
     var timer=setInterval(function () {
                    $this.text(countdown);
                    countdown-=1;
                    //alert('邮箱验证码发送成功！');
                    if(countdown<=0){
                        clearInterval(timer);//清掉定时器
                        $this.text('获取验证码');//将按钮的文字修改回来
                        bindEmailCaptchaClick();//重新绑定点击事件
                    }
                },1000);

     $this.off('click');//这句写了之后，下边的语句都不好使了，这句有问题，这句应该放在最后
     $.ajax({
         url:"/auth/captcha/email?email="+email,
         method:"GET",
         success:function (result) {
            var code=result['code'];
            //alert(code);
            if(code!=200){
                alert(result['message']);
            }
         },
         error:function (error) {
             console.log(error)

         }
     })
 });
}
$(function () {
     bindEmailCaptchaClick();
});//写function之后，这里边的代码就可以在页面代码全部加载完成之后，再执行这个function代码