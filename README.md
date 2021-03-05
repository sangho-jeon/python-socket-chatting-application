# python-socket-chatting-application


### python을 이용한 socket통신 chatting console application. 

#### server설명
python select 모듈을 이용해 non blocking 서버를 구현했습니다. command들의 넘버링에 따라 내부 로직이 돌아가고 client로 response합니다. 

#### client설명
sending thread와 receive thread를 만들어 전송과 수신이 동시에 일어날 수 있게 하였습니다. 각 command들을 설정해 여러 기능들을 수행합니다.




## commands

\users: 현재 채팅방의 이용자들의 정보와 인원을 알려줍니다. 

\wh : whisper의 기능으로 특정 이용자에게 귓속말을 보냅니다.

\fsend: file send로 모든 이용자들에게 보낼 파일을 전송시킬수 있습니다.

\rename: 아이디를 변경할 수 있습니다. 만일 중복된 아이디라면 변경할 수 없습니다. 

\rtt: 서버와의 response time을 알려줍니다.

\exit: 어플리케이션을 종료합니다.
