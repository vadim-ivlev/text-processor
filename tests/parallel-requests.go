package main

import {
	"fmt"
}



func main(){
	var N = 10
	var c = make(chan []string)

	for i := 0; i < N; i++ {
		go doRequest(c)
	}


	for i := 0; i < N; i++ {
		s<-c
		fmt.Println(s)
	}
}

func doRequest(c chan []string){
	
}