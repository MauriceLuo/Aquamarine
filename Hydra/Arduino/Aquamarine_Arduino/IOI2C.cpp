#include "IOI2C.h"

void IIC_Init(void)
{
  pinMode(SCL_pin, OUTPUT);  // 设置D7为输出
  pinMode(SDA_pin, OUTPUT);    // 设置D6为输入 INPUT

	digitalWrite(SDA_pin, HIGH);	  	  
	digitalWrite(SCL_pin, HIGH);
}

void IIC_Start(void)
{
	pinMode(SDA_pin, OUTPUT);    
	digitalWrite(SDA_pin, HIGH);	  	  
	digitalWrite(SCL_pin, HIGH);
	
	delayMicroseconds(5);
 	digitalWrite(SDA_pin, LOW);//START:when CLK is high,DATA change form high to low 
	
	delayMicroseconds(5);
	digitalWrite(SCL_pin, LOW);
}
	  
void IIC_Stop(void)
{
  pinMode(SDA_pin, OUTPUT);
  digitalWrite(SCL_pin, LOW);
  digitalWrite(SDA_pin, LOW);//STOP:when CLK is high DATA change form low to high

  delayMicroseconds(5);
  digitalWrite(SCL_pin, HIGH); 
  digitalWrite(SDA_pin, HIGH);

  delayMicroseconds(5);							   	
}

uint8_t IIC_Wait_Ack(void)
{
	uint8_t ucErrTime=0; 
	pinMode(SDA_pin, INPUT);     
	digitalWrite(SDA_pin, HIGH);
  delayMicroseconds(5);	  
	while(digitalRead(SDA_pin))
	{
		ucErrTime++;
		if(ucErrTime>50)
		{
			IIC_Stop();
			return 1;
		}
		delayMicroseconds(5);
	}  
	digitalWrite(SCL_pin, HIGH);
	delayMicroseconds(5); 
	digitalWrite(SCL_pin, LOW);
	return 0;  
} 

void IIC_Ack(void)
{
	digitalWrite(SCL_pin, LOW);
	pinMode(SDA_pin, OUTPUT);
	digitalWrite(SDA_pin, LOW);
  delayMicroseconds(5);
	digitalWrite(SCL_pin, HIGH);
  delayMicroseconds(5);
	digitalWrite(SCL_pin, LOW);
}
	    
void IIC_NAck(void)
{
	digitalWrite(SCL_pin, LOW);
	pinMode(SDA_pin, OUTPUT);
	digitalWrite(SDA_pin, HIGH);
	
  delayMicroseconds(5);
	digitalWrite(SCL_pin, HIGH);
  delayMicroseconds(5);
	digitalWrite(SCL_pin, LOW);
}					 				     
		  
void IIC_Send_Byte(uint8_t txd)
{                        
  uint8_t t; 
  pinMode(SDA_pin, OUTPUT); 	    
  digitalWrite(SCL_pin, LOW);
  for(t=0;t<8;t++)
  {              
    if((txd&0x80)>>7)
    {
      digitalWrite(SDA_pin, HIGH);
    }else{
      digitalWrite(SDA_pin, LOW);
    }
    txd<<=1; 	  
    delayMicroseconds(2);   
    digitalWrite(SCL_pin, HIGH);
    delayMicroseconds(5);
    digitalWrite(SCL_pin, LOW);	
    delayMicroseconds(3);
  }	 
} 	 
  
uint8_t IIC_Read_Byte(unsigned char ack)
{
	unsigned char i,receive=0;
	pinMode(SDA_pin, INPUT);
    for(i=0;i<8;i++ )
	  {
      digitalWrite(SCL_pin, LOW); 
        
		  delayMicroseconds(5);
		  digitalWrite(SCL_pin, HIGH);
      receive<<=1;
      if(digitalRead(SDA_pin))receive++;   
		
		delayMicroseconds(5); 
    }					 
    if (ack)
        IIC_Ack(); 
    else
        IIC_NAck();
    return receive;
}

int32_t IICreadBytes(uint8_t dev, uint8_t reg, uint8_t *data, uint32_t length)
{
    uint32_t count = 0;

    IIC_Start();
    IIC_Send_Byte(dev);	
    if(IIC_Wait_Ack() == 1)return 0;
    IIC_Send_Byte(reg);
    if(IIC_Wait_Ack() == 1)return 0;
    IIC_Start();
    IIC_Send_Byte(dev+1); 
    if(IIC_Wait_Ack() == 1)return 0;

    for(count=0; count<length; count++)
    {
        if(count!=length-1)data[count]=IIC_Read_Byte(1);
        else  data[count]=IIC_Read_Byte(0);	 
    }
    IIC_Stop();
    return 1;
}


int32_t IICwriteBytes(uint8_t dev, uint8_t reg, uint8_t* data, uint32_t length)
{
    uint32_t count = 0;
    IIC_Start();
    IIC_Send_Byte(dev);	   
    if(IIC_Wait_Ack() == 1)return 0;
    IIC_Send_Byte(reg);   
    if(IIC_Wait_Ack() == 1)return 0;
    for(count=0; count<length; count++)
    {
        IIC_Send_Byte(data[count]);
        if(IIC_Wait_Ack() == 1)return 0;
    }
    IIC_Stop();

    return 1; 
}
