package main

import (
	"database/sql"
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"strconv"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

func sec(duration time.Duration) float64 {
	return float64(duration/time.Millisecond) / 1000
}

func readCsvFile(filePath string) [][]string {
	f, err := os.Open(filePath)
	if err != nil {
		log.Fatal("Unable to read input file "+filePath, err)
	}
	defer f.Close()

	csvReader := csv.NewReader(f)
	records, err := csvReader.ReadAll()
	if err != nil {
		log.Fatal("Unable to parse file as CSV for "+filePath, err)
	}

	return records
}

// Печатаем сообщение об ошибке
func checkErr(err error) {
	if err != nil {
		fmt.Print(err)
	}
}

func readSQLite(fileName, sqlText string) [][]string {
	res := make([][]string, 0)
	db, err := sql.Open("sqlite3", fileName)
	defer db.Close()
	checkErr(err)

	rows, err := db.Query(sqlText)
	checkErr(err)
	var index int
	var objid int
	var lemmatized_text string

	for rows.Next() {
		err = rows.Scan(&index, &objid, &lemmatized_text)
		checkErr(err)
		r := []string{strconv.Itoa(objid), lemmatized_text}
		res = append(res, r)
	}

	rows.Close()
	return res
}

func processRecords(records [][]string) int64 {
	// le := len(records)
	var counter int64
	for _, rec := range records {
		counter += int64(len(rec[1]))
	}
	return counter
}

func main() {
	fmt.Println("reading css")
	startTime := time.Now()
	records := readCsvFile("/Volumes/ssd/dumps/articles_i.csv")
	duration := time.Since(startTime)

	fmt.Printf("%d css записей загружено за %.2f sec.", len(records), sec(duration))

	startTime = time.Now()
	n := processRecords(records)
	duration = time.Since(startTime)

	fmt.Printf("Обработано %d символов за %.4f sec.\n", n, sec(duration))

	// ---------------------------------------------------------------------------------------
	fmt.Println("reading sqlite")
	startTime = time.Now()
	records = readSQLite("/Volumes/ssd/dumps/df.db", "select * from art")
	duration = time.Since(startTime)

	fmt.Printf("%d css записей загружено за %.2f sec.", len(records), sec(duration))

	startTime = time.Now()
	n = processRecords(records)
	duration = time.Since(startTime)

	fmt.Printf("Обработано %d символов за %.4f sec.\n", n, sec(duration))
}
