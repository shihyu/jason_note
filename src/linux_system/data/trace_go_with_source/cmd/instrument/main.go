package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"go/ast"
	"go/format"
	"go/parser"
	"go/token"
	"os"
	"path/filepath"
	"strings"
)

const tracerImport = "trace_go_with_source/tracer"

// Overlay is the JSON structure for go build -overlay
type Overlay struct {
	Replace map[string]string `json:"Replace"`
}

func usage() {
	fmt.Fprintf(os.Stderr, "用法:\n")
	fmt.Fprintf(os.Stderr, "  %s <source.go> [output.go]          # 直接模式\n", os.Args[0])
	fmt.Fprintf(os.Stderr, "  %s -overlay <tmpdir> <source.go...>  # overlay 模式（不動原始碼）\n", os.Args[0])
	os.Exit(1)
}

func main() {
	if len(os.Args) < 2 {
		usage()
	}

	if os.Args[1] == "-overlay" {
		runOverlayMode()
	} else {
		runDirectMode()
	}
}

// runOverlayMode instruments files into tmpdir and writes overlay.json
func runOverlayMode() {
	if len(os.Args) < 4 {
		usage()
	}

	tmpDir := os.Args[2]
	srcFiles := os.Args[3:]

	if err := os.MkdirAll(tmpDir, 0755); err != nil {
		fmt.Fprintf(os.Stderr, "建立目錄失敗: %v\n", err)
		os.Exit(1)
	}

	overlay := Overlay{Replace: make(map[string]string)}

	for _, src := range srcFiles {
		absSrc, err := filepath.Abs(src)
		if err != nil {
			fmt.Fprintf(os.Stderr, "取得絕對路徑失敗: %v\n", err)
			os.Exit(1)
		}

		outPath := filepath.Join(tmpDir, filepath.Base(src))
		if err := instrumentFile(src, outPath); err != nil {
			fmt.Fprintf(os.Stderr, "插樁 %s 失敗: %v\n", src, err)
			os.Exit(1)
		}

		overlay.Replace[absSrc] = outPath
		fmt.Fprintf(os.Stderr, "插樁: %s -> %s\n", src, outPath)
	}

	overlayPath := filepath.Join(tmpDir, "overlay.json")
	data, err := json.MarshalIndent(overlay, "", "  ")
	if err != nil {
		fmt.Fprintf(os.Stderr, "JSON 序列化失敗: %v\n", err)
		os.Exit(1)
	}

	if err := os.WriteFile(overlayPath, data, 0644); err != nil {
		fmt.Fprintf(os.Stderr, "寫入 overlay.json 失敗: %v\n", err)
		os.Exit(1)
	}

	// Print overlay path to stdout for Makefile to capture
	fmt.Print(overlayPath)
}

// runDirectMode instruments a single file (original behavior)
func runDirectMode() {
	srcFile := os.Args[1]
	outFile := ""
	if len(os.Args) >= 3 {
		outFile = os.Args[2]
	}

	if outFile == "" {
		ext := filepath.Ext(srcFile)
		base := strings.TrimSuffix(srcFile, ext)
		outFile = base + "_instrumented" + ext
	}

	if err := instrumentFile(srcFile, outFile); err != nil {
		fmt.Fprintf(os.Stderr, "%v\n", err)
		os.Exit(1)
	}

	fmt.Printf("已插樁: %s -> %s\n", srcFile, outFile)
}

func instrumentFile(srcFile, outFile string) error {
	fset := token.NewFileSet()
	node, err := parser.ParseFile(fset, srcFile, nil, parser.ParseComments)
	if err != nil {
		return fmt.Errorf("解析失敗: %w", err)
	}

	pkgName := node.Name.Name

	addImport(node, tracerImport)

	for _, decl := range node.Decls {
		fn, ok := decl.(*ast.FuncDecl)
		if !ok || fn.Body == nil {
			continue
		}

		funcName := buildFuncName(pkgName, fn)
		traceStmt := buildTraceStmt(funcName)
		fn.Body.List = append([]ast.Stmt{traceStmt}, fn.Body.List...)
	}

	var buf bytes.Buffer
	if err := format.Node(&buf, fset, node); err != nil {
		return fmt.Errorf("格式化失敗: %w", err)
	}

	return os.WriteFile(outFile, buf.Bytes(), 0644)
}

func buildFuncName(pkg string, fn *ast.FuncDecl) string {
	if fn.Recv == nil || len(fn.Recv.List) == 0 {
		return pkg + "." + fn.Name.Name
	}

	recv := fn.Recv.List[0]
	var typeName string
	switch t := recv.Type.(type) {
	case *ast.StarExpr:
		if ident, ok := t.X.(*ast.Ident); ok {
			typeName = "(*" + ident.Name + ")"
		}
	case *ast.Ident:
		typeName = t.Name
	}

	if typeName != "" {
		return pkg + "." + typeName + "." + fn.Name.Name
	}
	return pkg + "." + fn.Name.Name
}

func buildTraceStmt(funcName string) *ast.DeferStmt {
	return &ast.DeferStmt{
		Call: &ast.CallExpr{
			Fun: &ast.CallExpr{
				Fun: &ast.SelectorExpr{
					X:   ast.NewIdent("tracer"),
					Sel: ast.NewIdent("Trace"),
				},
				Args: []ast.Expr{
					&ast.BasicLit{
						Kind:  token.STRING,
						Value: fmt.Sprintf("%q", funcName),
					},
				},
			},
		},
	}
}

func addImport(file *ast.File, importPath string) {
	for _, imp := range file.Imports {
		if imp.Path.Value == fmt.Sprintf("%q", importPath) {
			return
		}
	}

	newImport := &ast.ImportSpec{
		Path: &ast.BasicLit{
			Kind:  token.STRING,
			Value: fmt.Sprintf("%q", importPath),
		},
	}

	for _, decl := range file.Decls {
		genDecl, ok := decl.(*ast.GenDecl)
		if !ok || genDecl.Tok != token.IMPORT {
			continue
		}
		genDecl.Specs = append(genDecl.Specs, newImport)
		return
	}

	genDecl := &ast.GenDecl{
		Tok:   token.IMPORT,
		Specs: []ast.Spec{newImport},
	}
	file.Decls = append([]ast.Decl{genDecl}, file.Decls...)
}
