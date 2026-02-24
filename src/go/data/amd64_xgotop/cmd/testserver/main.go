package main

import (
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
)

func main() {
	r := mux.NewRouter()
	r.HandleFunc("/books/{title}/page/{page}", GetPage)
	http.ListenAndServe(":80", r)
}

func GetPage(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	title := vars["title"]
	page := vars["page"]

	w.Header().Set("Access-Control-Allow-Origin", "*")

	fmt.Fprintf(w, "You've requested the book: %s on page %s, req @ (%p, %p, %p)\n", title, page, r, &r.Method, r.URL)
}
