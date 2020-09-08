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


//  записывает результат запроса в канал
func doRequest(с ) {
	client := http.Client{
		Timeout: time.Duration(requestTimeout) * time.Second,
	}

	req, err := http.NewRequest("GET", fmt.Sprintf(urlArticle, id), nil)
	if err != nil {
		fmt.Println(err)
	}
	req.Close = true
	req.Header.Set("Connection", "close")

	resp, err := client.Do(req)

	// resp, err := http.Get(fmt.Sprintf(urlArticle, id))
	if err != nil {
		fmt.Println(err)
		return []string{id, ""}
	}
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Println(err)
		return []string{id, ""}
	}
	s := string(body)
	return []string{id, s}
}
