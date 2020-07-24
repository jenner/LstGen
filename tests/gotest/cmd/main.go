package main

import (
	"fmt"
	"github.com/shopspring/decimal"
	"gotest.test/tax"
)

func main() {
	lst := tax.New()
	lst.SetRe4(decimal.NewFromInt(50_000_00))  // in cents
	lst.SetPkv(1)
	lst.SetAlter1(0)
	lst.SetAf(0)
	lst.SetF(1)
	lst.SetPvs(0)
	lst.SetR(0)
	lst.SetLzzhinzu(decimal.NewFromInt(0))
	lst.SetPvz(0)
	lst.SetStkl(1)
	lst.SetLzz(2)
	lst.SetKrv(2)
	lst.MAIN()
	steuer := lst.GetLstlzz().Add(lst.GetStv().Add(lst.GetSts()))
	soli := lst.GetSolzlzz().Add(lst.GetSolzs().Add(lst.GetSolzv()))
	res := steuer.Add(soli).Div(decimal.NewFromInt(100))
	fmt.Printf("%v\n", res.StringFixed(2))
}

